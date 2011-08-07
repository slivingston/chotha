"""Handles the creation and maintenance of the wordcloud."""
import apsw, re

def get_real_words(orig_text):
  words = re.findall(r'\b[a-z]+\b', orig_text, re.I)
  return set(words)

def update_word_cloud(oldtext, newtext, dbname):
  """Passed two blocks of text, corresponding to the old and new version of the
  note body, split them both into words, find out which words have been removed
  which have been added and remove/add them to the word cloud ."""
  oldwords = get_real_words(oldtext)
  newwords = get_real_words(newtext)
  words_removed = oldwords - newwords #Ain't Python cool
  words_added = newwords - oldwords #Repeat with me, ain't Python cool
  
  conn = apsw.Connection(dbname)
  c = conn.cursor()
  for word in words_removed:
    c.execute('UPDATE wordcloud SET count=count-1 WHERE word=?', (word,)) 

  #Clean it up
  c.execute('DELETE FROM wordcloud WHERE count < 1')
    
  for word in words_added:
    c.execute('UPDATE wordcloud SET count=count+1 WHERE word=?', (word,)) 
    if conn.changes() == 0:
      c.execute('INSERT INTO wordcloud (word,count) VALUES (?,1)', (word,))
 
def update_note(old_note, new_note, dbname): 
  update_word_cloud(old_note['body'], new_note['body'], dbname)
  
def rebuild_wordcloud(notes, dbname):
  """This could take a long, long time."""
  conn = apsw.Connection(dbname)
  c = conn.cursor()
  c.execute('DELETE FROM wordcloud')
  total = len(notes)
  for n,note in enumerate(notes):
    update_word_cloud('', note['body'], dbname)
    if n % 10:
      print '%0.0f%% done' %(100.*n/total)